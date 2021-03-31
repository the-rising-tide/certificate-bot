import logging
import time
from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Row
from sqlalchemy.orm import sessionmaker
import dateparser

import utils.utils as utl
import core.db_models as dbm
import core.request_cert as req_ct

engine = create_engine('sqlite:///data/main.db', echo=True)


def cycle_certs() -> List[Tuple[int, str]]:
    """
    Request all domains ordered by user\n
    for User1: domain1, domain2\n
    for User2: domain1, ...

    Registers when:\n
    - dates of certificate change
    - the cert expires in less than 7 days\n

    Saves this updates in a list that the bot can iterate over to dispatch the information

    :return: List of Tuples(chat_id, update as string)
    """
    session = sessionmaker(bind=engine)()
    # TODO: Make this query better. It is likely to fail when user base grows to big
    users = session.query(dbm.Users).all()

    updates: List[Tuple[int, str]] = []
    logging.info(f"Starting requests for {len(users)} users")
    checked = 0
    errors = 0
    for user in users:

        statement: List[Row] = select(dbm.Domains).where(dbm.Domains.chat_id == user.chat_id)
        # extract entry objects from row objects
        domains = [e[0] for e in session.execute(statement).all()]

        for domain in domains:
            # get cert dict
            cert = req_ct.get_cert(domain.domain, domain.port)

            # what if there is no longer a cert?
            # Remove it from db add waring message and continue
            if not cert:
                errors += 1
                message = utl.prep_for_md(f'*ERROR!*\nThere is no certificate for {utl.mk_link(domain.domain, domain.port)}\n'
                          f'Please check your certificate _immediately_!'
                          f'_This domain was removed from your watchlist. You can add it again after it got a new cert._',
                                          ignore=['*', '_'])
                updates.append((user.chat_id, message))
                session.query(dbm.Domains).filter(dbm.Domains.domain == domain.domain).delete()
                session.commit()
                logging.warning(f"{domain.domain}:{domain.port} expired, removed it from database")
                continue

            # extract potential new dates - removing timezone information
            new_before = dateparser.parse(cert['notBefore']).replace(tzinfo=None)
            new_after = dateparser.parse(cert['notAfter']).replace(tzinfo=None)

            # new_before = datetime.today()
            # check whether something has changed from the expected dates
            if domain.not_before != new_before or domain.not_after != new_after:
                # print("IS NOT EQUAL")
                message = utl.prep_for_md(f"The cert of {domain.domain} - Port {domain.port} has changed:\n"
                          f"notBefore: from {domain.not_before.replace(microsecond=0)} to {new_before.replace(microsecond=0)}\n"
                          f"notAfter: {domain.not_after.replace(microsecond=0)} to {new_after.replace(microsecond=0)}")

                # append update message
                updates.append((user.chat_id, message))

                # update database object
                domain.not_before = new_before
                domain.not_after = new_after
                domain.last_checked = datetime.today()

            # new_after = datetime.today() - timedelta(2)
            # check whether cert expires in less then a week
            delta = new_after - datetime.today()
            if delta < timedelta(utl.NOTIFY_BEFORE):
                print("EXPIRES!")
                message = utl.prep_for_md(f'The certificate for {domain.domain} - Port {domain.port} will expire in:\n'
                                          f'*{delta.days} days*\n'
                                          f'Expiry: {new_after.replace(microsecond=0)}', ignore=['*'])
                updates.append((user.chat_id, message))

            # update last checked information and commit update
            domain.last_checked = datetime.today()
            session.add(domain)
            session.commit()
            checked += 1
            # sleeping a sec to not look like a ddos attack
            time.sleep(1)

    if errors:
        logging.warning(f"Finished {checked} requests with {errors} errors")
    else:
        logging.info(f"Finished {checked} daily cert requests")
    return updates


if __name__ == '__main__':
    update_list = cycle_certs()
    print(update_list)
